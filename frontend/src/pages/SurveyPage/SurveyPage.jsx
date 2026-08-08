import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import "./SurveyPage.css";
import SurveyForm from "../../components/SurveyForm/SurveyForm";
import ErrorPopup from "../../components/ErrorPopup/ErrorPopup";

// Backend routing helpers
const LEGACY_API_BASE = process.env.REACT_APP_API_ADDRESS;
const DASS_MULTICLASS_API_BASE = process.env.REACT_APP_DASS_MULTICLASS_API_ADDRESS;

// Decide whether this survey should use the modern backend (sklearn 1.4.2)
function isDassMulticlassSurvey(pythonSurveyName, surveyObj) {
  const surveyId = surveyObj?.survey_id;
  const surveyMode = surveyObj?.survey_mode;

  return (
    pythonSurveyName === "anxiety_multiclass" || // from URL: anxiety-multiclass
    surveyId === "dass_multiclass" ||            // backend survey_id for multiclass
    surveyMode === "anxiety-multiclass"          // explicit survey_mode
  );
}

function pickApiBaseForSurvey(pythonSurveyName, surveyObj) {
  return isDassMulticlassSurvey(pythonSurveyName, surveyObj)
    ? DASS_MULTICLASS_API_BASE
    : LEGACY_API_BASE;
}

function SurveyPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [description, setDescription] = useState([]);
  const split = window.location.pathname.split("/");
  const totalQuestions = useRef(0);
  const surveyName = split[2];
  const [survey, setSurvey] = useState({});
  const [currentPage] = useState(0);
  // error handling
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  // get time when survey is loaded
  const startTime = useRef(new Date());
  useEffect(() => {
  const getSurveyData = async () => {
    const pythonSurveyName = surveyName.replaceAll("-", "_");

    // Decide which backend to use for this survey
    const apiBase = pickApiBaseForSurvey(pythonSurveyName, null);

    const response = await axios.get(
      `${apiBase}/survey/${pythonSurveyName}`
    );
    setSurvey(response.data);
  };
    getSurveyData();
  }, [surveyName]);

  useEffect(() => {
    const surveyQuestions = survey?.questions ?? {};
    totalQuestions.current = Object.keys(surveyQuestions).length;
  }, [survey]);

  const submitSurvey = async (surveyResponses) => {
    const valid = validateResponses(surveyResponses);
    if (!valid) {
      setShowError(true);
      setErrorMessage("You must fill out all survey questions.");
    } else if (survey.survey_id === "manga") {
      navigate(location.pathname + "/completed");
    } else {
      // get end time when survey is submitted
      const endTime = new Date();
      // calculate time duration to complete survey
      const response_duration = (endTime - startTime.current) / 1000;

      // Decide backend based on this survey
      const pythonSurveyName = surveyName.replaceAll("-", "_");
      const apiBaseForPost = pickApiBaseForSurvey(pythonSurveyName, survey);

      const response = await axios.post(
        `${apiBaseForPost}/results`,
        {
          survey: survey.survey_id,
          mode: survey.survey_mode,
          data: surveyResponses,
          duration: response_duration,
        }
      );
      navigate(location.pathname + "/results", { state: response.data });
    }
  };

  const validateResponses = (surveyResponses) => {
    for (const response in surveyResponses) {
      if (surveyResponses[response] === null) {
        return false;
      }
    }
    return true;
  };

  useEffect(() => {
    if (survey !== "not-found") {
      const paragraphs = [];
      for (const property in survey?.description) {
        paragraphs.push(<p key={property}>{survey?.description[property]}</p>);
      }
      setDescription(paragraphs);
    }
  }, [survey]);

  if (survey === "not-found") {
    return (
      <div className="survey-page-container">
        <h3>404. Not Found.</h3>
      </div>
    );
  } else if (Object.keys(survey).length === 0) {
    return (
      <div className="survey-page-container">
        <h3>Fetching survey...</h3>
      </div>
    );
  } else {
    return (
      <div className="survey-page-container">
        {showError && (
          <ErrorPopup message={errorMessage} setShowError={setShowError} />
        )}
        <h3>Welcome to the {survey?.title} interactive webpage.</h3>
        <div className="description-container">{description}</div>
        <div className="survey-container">
          <SurveyForm
            key={survey?.title}
            submitSurvey={submitSurvey}
            data={survey?.pages[currentPage]}
            page={currentPage}
          />
        </div>
      </div>
    );
  }
}

export default SurveyPage;
