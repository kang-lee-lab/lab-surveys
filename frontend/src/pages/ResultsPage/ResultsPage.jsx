import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  PieChart,
  Pie,
  Tooltip,
  Label,
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from "recharts";
import { getCleanSurveyData } from "../../utils/helper";
import DassMulticlassChart from "./DassMulticlassChart"; 

function ResultsPage() {
  // get the data from SurveyPage component
  const location = useLocation();
  // location.state holds result data sent from the backend
  const data = location.state;
  console.log(data);
  const surveyId = data.metadata.survey_id;
  // format survey data specific to what graph is being used
  const cleanData = getCleanSurveyData(surveyId, data);
  // try again button
  const split = window.location.pathname.split("/");
  const surveyName = split[2];
  const navigate = useNavigate();
  const returnToSurvey = () => {
    const pythonSurveyName = surveyName.replaceAll("-", "_");
    let path = `/survey/${pythonSurveyName}`;
    navigate(path);
  };
  // return to home button
  const returnToHome = () => {
    let path = `/`;
    navigate(path);
  };

  return (
    <div className="survey-page-container">
      <h3>
        Welcome to the results page for the {data.metadata.full_name} survey.
      </h3>
      {surveyId === "dass" && (
        <div>
          <h1>Your likelihood of moderate {data.mode} is {(data.positive*100).toFixed(2)}%.</h1>
          <p>Displayed is your estimated likelihood of moderate {data.mode} given your answers to the DASS questions. 
          This is calculated through a machine learning model trained using data collected from an online survey.</p>
          <div style={{ display: "flex", justifyContent: "center" }}>
            <PieChart width={1000} height={500}>
              <Tooltip />
              <Pie
                data={cleanData}
                cx={500}
                cy={220}
                innerRadius={110}
                outerRadius={160}
                paddingAngle={0}
                dataKey="value"
              >
                <Label
                  value={`${(data.positive * 100).toFixed(2)}%`}
                  position="center"
                  fill="#000"
                  fontSize={20}
                  fontWeight="bold"
                />
              </Pie>
            </PieChart>
          </div>
        </div>
      )}
      {surveyId === "nafld" && (
        <div>
          <h1>Your likelihood of NAFLD is {(data.positive*100).toFixed(2)}%.</h1>
          <p>Displayed is your estimated likelihood of Non-Alcoholic Fatty Liver Disease (NAFLD) given your physical measurements and blood biomarkers. 
            This is calculated through a machine learning model trained using patient data.</p>
          <div style={{ display: "flex", justifyContent: "center" }}>
            <PieChart width={1000} height={500}>
              <Tooltip />
              <Pie
                data={cleanData}
                cx={500}
                cy={220}
                innerRadius={110}
                outerRadius={160}
                paddingAngle={0}
                dataKey="value"
              >
                <Label
                  value={`${(data.positive * 100).toFixed(2)}%`}
                  position="center"
                  fill="#000"
                  fontSize={20}
                  fontWeight="bold"
                />
              </Pie>
            </PieChart>
          </div>
        </div>
      )}
      {surveyId === "mmpi" && (
        <div>
          <h1>Your likelihood of being positive in each condition is: </h1>
          <table className="table" style={{ width: "100%" }}>
            <tbody>
              <tr>
                <th style={{ textAlign: "left" }}>Condition</th>
                <th style={{ textAlign: "left" }}>Likelihood</th>
              </tr>
              <tr>
                <td>Depression (DT)</td>
                <td>{(cleanData.find(item => item.name === 'DT').x * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Hypochondriasis (HsT)</td>
                <td>{(cleanData.find(item => item.name === 'HsT').x * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Hysteria (HyT)</td>
                <td>{(cleanData.find(item => item.name === 'HyT').x * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Psychopathic Deviate (PdT)</td>
                <td>{(cleanData.find(item => item.name === 'PdT').x * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Masculinity (MfT)</td>
                <td>{(cleanData.find(item => item.name === 'MfT').x * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Paranoia (PaT)</td>
                <td>{(cleanData.find(item => item.name === 'PaT').x * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Psychasthenia (PtT)</td>
                <td>{(cleanData.find(item => item.name === 'PtT').x * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Schizophrenia (ScT)</td>
                <td>{(cleanData.find(item => item.name === 'ScT').x * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Hypomania (MaT)</td>
                <td>{(cleanData.find(item => item.name === 'MaT').x * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Social Introversion (SiT)</td>
                <td>{(cleanData.find(item => item.name === 'SiT').x * 100).toFixed(2)}%</td>
              </tr>
            </tbody>
          </table>
          <p>
          Displayed below is a graph depicting your likelihood of being positive in each condition of the MMPI.
          </p>
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
          <RadarChart height={500} width={500} outerRadius="90%" data={cleanData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="name" />
            <PolarRadiusAxis />
            
            <Radar dataKey="a" stroke="grey" fill = "red" fillOpacity={0.5} />
            <Radar dataKey="b" stroke="grey" fill = "yellow" fillOpacity={0.5} />
            <Radar dataKey="c" stroke="grey" fill = "green" fillOpacity={0.5} />
            <Radar dataKey="x" stroke="darkgrey" fill="grey" fillOpacity={0.75} />
          </RadarChart>       
        </div>
        </div>
      )}
      {surveyId === "childbmi" && (
        <div>
          <h4>At age {data.age_to_predict}, </h4>
          <h4>The child's predicted height is {(data.pred_height).toFixed(2)} cm.</h4>
          <h4>The child's predicted weight is {(data.pred_weight).toFixed(2)} kg.</h4>
            <h4>The child's predicted BMI is {(data.pred_bmi.toFixed(2))} kg/m<sup>2</sup>.</h4>
          <p>
            Displayed is your children's future height, weight, and BMI given
            their current physical measurements. This is calculated through a
            machine learning model trained using patient data.
          </p>
        </div>
      )}
      {surveyId === "asq" && (
        <div>
          <h1>Your ASQ is {data.asq_result}. </h1>
          <p>
            Your ASQ is an indication of your overall stress level. The table below can be used to interpret your score. 
          </p>
          <table className="table" style={{ width: "100%" }}>
            <tbody>
              <tr>
                <th style={{ textAlign: "left" }}>ASQ Range</th>
                <th style={{ textAlign: "left" }}>ASQ Classification</th>
              </tr>
              <tr>
                <td>80 and over</td>
                <td>Very High Stress</td>
              </tr>
              <tr>
                <td>70-79</td>
                <td>High Stress</td>
              </tr>
              <tr>
                <td>60-69</td>
                <td>Slightly High Stress</td>
              </tr>
              <tr>
                <td>41-59</td>
                <td>Average</td>
              </tr>
              <tr>
                <td>31-40</td>
                <td>Slightly Low Stress</td>
              </tr>
              <tr>
                <td>21-30</td>
                <td>Low Stress</td>
              </tr>
              <tr>
                <td>20 and below</td>
                <td>Very Low Stress</td>
              </tr>
            </tbody>
          </table>

          <p>
            Displayed below are your Stress Quotients for factors 1-6 (SQ1-6). Each SQ is unique and contributes to your overall Average Stress Quotient (ASQ).
          </p>
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
            <RadarChart
              height={500}
              width={500}
              outerRadius="80%"
              data={cleanData}
            >
              <PolarGrid />
              <PolarAngleAxis dataKey="name" />
              <PolarRadiusAxis />
              <Radar dataKey="x" stroke="grey" fill="grey" fillOpacity={0.5} />
            </RadarChart>
          </div>
        </div>
      )}
      {surveyId === "dass_multiclass" && (
        <div>
          <h1>Your predicted anxiety severity level is: {data.rank}.</h1>
          <p>Displayed is your estimated anxiety severity level given your answers to the selected DASS questions. 
          This is calculated through a machine learning model pre-trained using data collected from an online survey.</p>
          <div style={{ display: "flex", justifyContent: "center" }}>
            <DassMulticlassChart severityLevel={data.severity_level} />
          </div>
        </div>
      )}
      <p>
        *This webpage does not contain medical/health advice. This tool is
        intended for informational and educational purposes only, and should not
        be taken as a substitute for professional advice. Reliance on any
        information on the webpage is solely at your own risk.
      </p>
      <button
          id="try-again-button"
          onClick={returnToSurvey}
          style={{ float: 'left' }}
        >
          <span>Try Again</span>
      </button>
      <button
          id="home-button"
          onClick={returnToHome}
          style={{ float: 'right' }}
        >
          <span>Return to Home</span>
      </button>
    </div>

  );
}

export default ResultsPage;
