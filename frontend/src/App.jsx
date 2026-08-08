import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
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
    <Router>
      <Header />
      <div>
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path={"/participate"} element={<DataColSurveys/>} />
          <Route path="/participate/:name" element={<GeneralConsent />} />
          <Route path="/survey/:name/results" element={<ResultsPage />} />
          <Route path="/survey/:name" element={<SurveyPage />} />
            <Route path="/survey/consent/:name" element={<Consent />} />
            {/*<Route path={"/data-surveys"} element={<DataColSurveys/>} />*/}
            <Route path={"/survey/manga/completed"} element={<Completed />} />
            {/*<Route path={"/survey/history"} element={<History/>} />*/}
            <Route path={"/survey/:name/history"} element={<History />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
