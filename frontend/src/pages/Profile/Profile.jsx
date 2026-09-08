import React, { useEffect, useState } from "react";
import "./Profile.css";
import { API_BASE, UnauthorizedError, useApi } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";

function Profile() {
  const { request } = useApi();
  const { isAuthenticated, isLoading, email, login } = useAuth();
  const [responses, setResponses] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    // The SDK reports signed-out until it has restored the session, so acting
    // before that fetches without a token and 401s on every page load.
    if (isLoading) return;

    if (!isAuthenticated) {
      // Whatever is on screen belongs to the previous identity.
      setResponses([]);
      setError("");
      return;
    }

    let cancelled = false;
    setResponses([]);
    setError("");

    request({ method: "get", url: `${API_BASE}/participants/me/responses` })
      .then((response) => {
        if (!cancelled) setResponses(response.data);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(
          err instanceof UnauthorizedError
            ? "Your session expired. Please sign in again."
            : "Could not load your surveys."
        );
      });

    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, isLoading, request]);

  if (isLoading) {
    return (
      <div className="profile-container">
        <h1>My surveys</h1>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="profile-container">
        <h1>My surveys</h1>
        <p>Sign in to see the surveys you have completed.</p>
        <button className="auth-button" onClick={login}>
          Sign In
        </button>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <h1>My surveys</h1>
      {email && <p className="profile-email">Signed in as {email}</p>}
      {error && <p className="profile-error">{error}</p>}

      {!error && responses.length === 0 ? (
        <p>
          You have not completed any surveys yet. Surveys taken while signed out
          are not saved to your account.
        </p>
      ) : (
        <table className="profile-table">
          <thead>
            <tr>
              <th>Survey</th>
              <th>Results</th>
              <th>Date</th>
              <th>Time</th>
              <th>Duration (s)</th>
            </tr>
          </thead>
          <tbody>
            {responses.map((entry) => (
              <tr key={entry.id}>
                <td>{entry.response_type}</td>
                <td>
                  <ul className="profile-results">
                    {Object.entries(
                      JSON.parse(entry.response_results ?? "{}")
                    ).map(([label, value]) => (
                      <li key={label}>
                        {label}: {String(value)}
                      </li>
                    ))}
                  </ul>
                </td>
                <td>{entry.response_date}</td>
                <td>{entry.response_time}</td>
                <td>{entry.response_duration}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Profile;
