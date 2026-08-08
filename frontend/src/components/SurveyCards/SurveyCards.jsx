import React from "react";
import "./SurveyCards.css";
import { Link } from "react-router-dom";

function SurveyCards(props) {
  return (
    <div className="survey-cards">
      <h3>{props.survey.title}</h3>
      <p>{props.survey.description}</p>
      <Link to={"/survey/" + props.survey.link}>Take the survey</Link>
    </div>
  );
}

export default SurveyCards;
