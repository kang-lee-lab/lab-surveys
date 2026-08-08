import React, { useState } from "react";
import "./Consent.css";
import { useNavigate } from "react-router-dom";
import consentData from "../../data/consent/manga-consent.json";

function Consent() {
  const [isAgreed, setIsAgreed] = useState(false);
  const [isNextEnabled, setIsNextEnabled] = useState(false);
  let navigate = useNavigate();
  const split = window.location.pathname.split("/");
  const surveyName = split[3];

  const handleAgreeChange = (event) => {
    setIsAgreed(event.target.checked);
    setIsNextEnabled(event.target.checked);
  };

  const handleNextClick = () => {
    let path = `/survey/${surveyName}`;
    navigate(path);
  };

  return (
    <div className={"consent-container"}>
      <h1>{consentData.title}</h1>

      {Object.keys(consentData.sections).map((sectionName) => (
        <div key={sectionName}>
          <h2>{sectionName}</h2>
          <p>{consentData.sections[sectionName]}</p>
        </div>
      ))}
      <p>
        I have read the above and consent to have my child participate in this
        study.
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
        Yes, I consent to have my child participate in this study.
      </div>
      <div className={"agreeButton"}>
        <input type="checkbox" />
        No, I do not consent to have my child participate in this study.
      </div>

      <p>
        I have read the above and consent to participate in this study myself.
      </p>
      <div className={"agreeButton"}>
        <input type="checkbox" />
        Yes, I consent to participate in this study.
      </div>
      <div className={"agreeButton"}>
        <input type="checkbox" />
        No, I do not consent to participate in this study.
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
  );
}

export default Consent;
