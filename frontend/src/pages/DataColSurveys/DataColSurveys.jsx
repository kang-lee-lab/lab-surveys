import React from "react";
import "./DataColSurveys.css";
import ConsentSurveyCards from "../../components/ConsentSurveyCards/ConsentSurveyCards";
import dataCollectionSurveys from "../../data/data-collection-surveys.json";

function DataColSurveys() {
  return (
    <div className="datacolsurveys-container">
      <div className="description-container">
        <h2>Surveys for Data Collection</h2>
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

        <p>
          By taking part in the surveys below, your data will be collected for
          research purposes. Your data will be kept confidential and anonymized
          to protect your privacy. Your participation is completely voluntary,
          and you have the right to withdraw at any time without any
          consequences. If you have any questions about this process, or about
          your rights as a participant in the study, please contact the [insert
          contact here].
        </p>
      </div>
      <div className="survey-card-containers">
        <div className="datacollection-survey-container">
          <h2>Demo Survey for Data Collection</h2>
          {dataCollectionSurveys.map((item) => (
            <ConsentSurveyCards survey={item} key={item.key} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default DataColSurveys;
