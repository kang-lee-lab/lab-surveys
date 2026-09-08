import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Auth0ProviderWithNavigate from "./auth/Auth0ProviderWithNavigate";
import { AuthProvider } from "./contexts/AuthContext";
import Homepage from "./pages/Homepage/Homepage";
import Header from "./components/Header/Header";
import SurveyPage from "./pages/SurveyPage/SurveyPage";
import DataColSurveys from "./pages/DataColSurveys/DataColSurveys";
import ResultsPage from "./pages/ResultsPage/ResultsPage";
import Completed from "./pages/Completed/Completed";
import GeneralConsent from "./pages/GeneralConsent/GeneralConsent";
import Consent from "./pages/Consent/Consent";
import History from "./pages/History/History";

function App() {
  return (
    // The Auth0 provider sits inside the router so it can restore the page the
    // user was on via useNavigate after the login redirect.
    <Router>
      <Auth0ProviderWithNavigate>
        <AuthProvider>
          <Header />
          <div>
            <Routes>
              <Route path="/" element={<Homepage />} />
              <Route path={"/participate"} element={<DataColSurveys/>} />
              <Route path="/participate/:name" element={<GeneralConsent />} />
              <Route path="/survey/:name/results" element={<ResultsPage />} />
              <Route path="/survey/:name" element={<SurveyPage />} />
              <Route path="/survey/consent/:name" element={<Consent />} />
              <Route path={"/survey/manga/completed"} element={<Completed />} />
              <Route path={"/survey/:name/history"} element={<History />} />
            </Routes>
          </div>
        </AuthProvider>
      </Auth0ProviderWithNavigate>
    </Router>
  );
}

export default App;
