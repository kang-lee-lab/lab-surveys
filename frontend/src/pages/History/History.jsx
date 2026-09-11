import React, { useEffect, useState } from "react";
import "./History.css";
import { API_BASE, ForbiddenError, UnauthorizedError, useApi } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";
import physicalSurveys from "../../data/physical-surveys.json";
import physiologySurveys from "../../data/physiology-surveys.json";
import psychologySurveys from "../../data/psychology-surveys.json";

function History() {
  const [data, setData] = useState([]);
  const [error, setError] = useState("");
  const { request } = useApi();
  const { isAuthenticated, isLoading } = useAuth();
  const split = window.location.pathname.split("/");
  const surveyName = split[2];

  useEffect(() => {
    // Wait for the SDK to restore the session; it reports signed-out until it
    // has, which would fetch without a token and 401 on every page load.
    if (isLoading) return;

    let cancelled = false;
    const fetchData = async () => {
      // Response data belongs to whoever is signed in now, so drop whatever the
      // previous identity was shown before asking again.
      setData([]);
      setError("");
      try {
        const responseType = surveyName.replaceAll("-", "_");
        const response = await request({
          method: "get",
          url: `${API_BASE}/history/${responseType}/`,
        });
        if (!cancelled) setData(response.data);
      } catch (err) {
        if (cancelled) return;
        if (err instanceof UnauthorizedError) {
          setError("Sign in with a lab account to view response history.");
        } else if (err instanceof ForbiddenError) {
          setError("This account does not have access to response history.");
        } else {
          console.error("Error fetching data:", err);
          setError("Could not load response history.");
        }
      }
    };

    fetchData();
    return () => {
      cancelled = true;
    };
  }, [surveyName, request, isAuthenticated, isLoading]);

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
      const response = await request({
        method: "get",
        url: `${API_BASE}/download-csv`,
        responseType: "blob",
      });
      const blob = response.data;
      const url = window.URL.createObjectURL(new Blob([blob]));
      const a = document.createElement("a");
      a.href = url;
      a.download = "data.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      console.error("Error downloading CSV:", err);
      setError(
        err instanceof UnauthorizedError || err instanceof ForbiddenError
          ? "This account does not have access to the CSV export."
          : "Could not download the CSV."
      );
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

      {error && <p className="history-error">{error}</p>}

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
