import React from "react";
import "./ConsentSurveyCards.css";
import { Link } from "react-router-dom";

function ConsentSurveyCards(props) {
    return (
        <div className="survey-cards">
            <h3>{props.survey.title}</h3>
            <p>{props.survey.description}</p>
            <Link to={"/participate/" + props.survey.link + "_consent"}>Take the survey</Link>
        </div>
    );
}

export default ConsentSurveyCards;