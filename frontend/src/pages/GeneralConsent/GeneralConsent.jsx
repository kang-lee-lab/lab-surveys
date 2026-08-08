import React, {useEffect, useState} from "react";
import "./GeneralConsent.css";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function GeneralConsent() {
  const [consentForm, setConsentForm] = useState(null);
  const [isAgreed, setIsAgreed] = useState(false);
  const [isNextEnabled, setIsNextEnabled] = useState(false);
  const navigate = useNavigate();
  const split = window.location.pathname.split("/");
  const surveyName = split[2];

  const handleAgreeChange = (event) => {
    setIsAgreed(event.target.checked);
    setIsNextEnabled(event.target.checked);
  };

  const handleNextClick = () => {
    const pythonSurveyName = surveyName.split('_')[0];
    let path = `/survey/${pythonSurveyName}`;
    navigate(path);
    // let path = `/data-surveys`;
    // navigate(path);
  };

  useEffect(() => {
    const fetchConsentForm = async () => {
      try {
        const pythonSurveyName = surveyName.replaceAll("-", "_");
        const response = await axios.get(
            `${process.env.REACT_APP_API_ADDRESS}/participate/${pythonSurveyName}`
        );
        setConsentForm(response.data);
        // const consentFormData = await response.json();
        // setConsentForm(consentFormData);
      } catch (error) {
        console.error(error);
      }
    };
    fetchConsentForm();
  }, [surveyName]);


  return (
    <div className="general-consent-container">
      <div className="description-container">
        <h2>Participate in Our Studies</h2>
        <p>
          You are participating in {consentForm?.title} conducted by Kang Lee
          Lab. <br /> <br />
          {consentForm?.introduction} <br /> <br />
          <b> Purpose of the studies: </b> <br />
          {consentForm?.purpose} <br /> <br />
          <b> Risks: </b> <br />
          {consentForm?.risks} <br /> <br />
          <b> Benefits: </b> <br />
          {consentForm?.benefits} <br /> <br />
          <b> Study Procedures: </b> <br />
          {consentForm?.procedures} <br /> <br />
          <b> Data Collection and Confidentiality: </b> <br />
          {consentForm?.confidentiality} <br />
          {consentForm?.voluntary} <br /> <br />
          <b> Questions about the research? </b> <br />
          {consentForm?.contact} <br />
        </p>
        <div className={"agreeButton"}>
          <input
            type="checkbox"
            id="agree"
            name="agree"
            value="Agree"
            checked={isAgreed}
            onChange={handleAgreeChange}
          />
          I agree to allow my data to be collected for the purposes of academic
          research.
        </div>
        <div>
          <button
            onClick={handleNextClick}
            disabled={!isNextEnabled}
            style={{ marginTop: "10px" }}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

export default GeneralConsent;
