import React, { useEffect } from "react";
import "./Homepage.css";
import physicalSurveys from "../../data/physical-surveys.json";
import physiologySurveys from "../../data/physiology-surveys.json";
import psychologySurveys from "../../data/psychology-surveys.json";
import SurveyCards from "../../components/SurveyCards/SurveyCards";

function Homepage() {
  useEffect(() => {
    const apiBases = [
      process.env.REACT_APP_API_ADDRESS,
      process.env.REACT_APP_DASS_MULTICLASS_API_ADDRESS,
    ].filter(Boolean);

    [...new Set(apiBases)].forEach((apiBase) => {
      fetch(`${apiBase}/wakeup`).catch(() => {});
    });
  }, []);

  return (
    <div className="homepage-container">
      <div className="description-container">
        <h2>What We Study</h2>
        <p>
          Kang Lee Lab has conducted research in a variety of areas including:
          deception in children and adults, racial bias, bias reduction in
          children, and fraud among senior citizens. Our studies have also
          focused on understanding brain development and brain processes of
          infants and adults using neuroimaging technology called functional
          Near-Infrared Spectroscopy (fNIRS). We have also conducted research
          using transdermal optical imaging technology to measure physiological
          changes such as heart rate and blood pressure from a person's face.
        </p>
      </div>
      <div className="survey-card-containers">
        <div className="psychology-survey-container">
          <h2>Demo Psychology Surveys</h2>
          {psychologySurveys.map((item) => (
            <SurveyCards survey={item} key={item.title} />
          ))}
        </div>
        <div className="physiology-survey-container">
          <h2>Demo Physiology Surveys</h2>
          {physiologySurveys.map((item) => (
            <SurveyCards survey={item} key={item.title} />
          ))}
        </div>
        <div className="physical-survey-container">
          <h2>Demo Physical Surveys</h2>
          {physicalSurveys.map((item) => (
            <SurveyCards survey={item} key={item.title} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default Homepage;
