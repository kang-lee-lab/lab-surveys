import React, { useEffect, useState } from "react";
import "./History.css";
import axios from "axios";
import physicalSurveys from "../../data/physical-surveys.json";
import physiologySurveys from "../../data/physiology-surveys.json";
import psychologySurveys from "../../data/psychology-surveys.json";

function History() {
  const [data, setData] = useState([]);
  const split = window.location.pathname.split("/");
  const surveyName = split[2];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseType = surveyName.replaceAll("-", "_");
        const response = await axios.get(
          `${process.env.REACT_APP_API_ADDRESS}/history/${responseType}/`
        );
        setData(response.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [surveyName]);

  const formatAnswers = (answers, questions) => {
    const formattedAnswers = [];
    Object.entries(answers).forEach(([key, value]) => {
      const questionInfo = questions.find((q) => q.question_id === key);
      if (questionInfo) {
        const unit = questionInfo.question.unit || "";
        formattedAnswers.push({
          question: questionInfo.question_text,
          value: `${value} ${unit}`,
        });
      }
    });
    return formattedAnswers;
  };

  const formatResults = (results) => {
    const formattedResults = [];
    Object.entries(results).forEach(([key, value]) => {
      formattedResults.push({
        question: key,
        value: value,
      });
    });
    return formattedResults;
  };
  const formatTable = (formattedAnswers) => {
    return (
      <table className="nested-table">
        <thead>
          <tr>
            <th>Question</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {formattedAnswers.map((answer, index) => (
            <tr key={index}>
              <td>{answer.question}</td>
              <td>{answer.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  const history_data = data?.map((entry, i) => {
    const answers = JSON.parse(entry.response_answers);
    const questions = entry.questions || [];

    const formattedAnswers = formatAnswers(answers, questions);
    const formattedResults = formatResults(JSON.parse(entry.response_results));
    return (
      <tr key={i}>
        <td>{entry.id}</td>
        <td>{formatTable(formattedAnswers)}</td>
        <td>{formatTable(formattedResults)}</td>
        <td>{entry.response_date}</td>
        <td>{entry.response_time}</td>
        <td>{entry.response_duration}</td>
      </tr>
    );
  });

  const handleDownload = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_ADDRESS}/survey/download-csv`
      );
      const blob = await response.blob();
      const url = window.URL.createObjectURL(new Blob([blob]));
      const a = document.createElement("a");
      a.href = url;
      a.download = "data.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (error) {
      console.error("Error downloading CSV:", error);
    }
  };

  const responseType = surveyName.replaceAll("-", "_");

  return (
    <div className="history-container">
      <h1>
        {
          [...psychologySurveys, ...physiologySurveys, ...physicalSurveys].find(
            (survey) => survey.link === responseType.replace("_", "-")
          )?.title
        }{" "}
        History
      </h1>

      <button onClick={handleDownload}>Download CSV</button>
      <br />
      <br />
      <table className="main-table">
        <tr>
          <th>ID</th>
          <th>Response Answers</th>
          <th>Response Results</th>
          <th>Response Date</th>
          <th>Response Time</th>
          <th>Response Duration</th>
        </tr>
        {history_data}
      </table>
    </div>
  );
}

export default History;
