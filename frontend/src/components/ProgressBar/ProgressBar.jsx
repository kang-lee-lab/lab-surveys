import React, { useEffect, useState } from "react";
import "./ProgressBar.css";

function ProgressBar(props) {
  const [progressStyle, setProgressStyle] = useState({});

  useEffect(() => {
    const percentage = Math.round(
      (props.questionsFilled / props.totalQuestions) * 100
    );
    setProgressStyle({
      height: "100%",
      width: `${percentage}%`,
      backgroundColor: "#b3cce6",
      textAlign: "right",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
    });
  }, [props]);

  return (
    <div className="progress-container">
      <p>Progress</p>
      <div className="progress-label">{`${props.questionsFilled}/${props.totalQuestions}`}</div>
      <div className="progress-bar">
        <div className="filled-progress" style={progressStyle}></div>
      </div>
    </div>
  );
}

export default ProgressBar;
