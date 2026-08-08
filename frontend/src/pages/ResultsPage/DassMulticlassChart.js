import React, { PureComponent } from 'react';
import { PieChart, Pie, Cell, LabelList } from 'recharts';

const RADIAN = Math.PI / 180;
const data = [
  { name: 'Normal', value: 36, color: '#74C69D' },   // Normal
  { name: 'Mild', value: 36, color: '#28A745' },   // Mild
  { name: 'Moderate', value: 36, color: '#FFC107' },   // Moderate
  { name: 'Severe', value: 36, color: '#FD7E14' },   // Severe
  { name: 'Extremely Severe', value: 36, color: '#DC3545' },   // Extremely Severe
];
const cx = 250; // Center X
const cy = 250; // Center Y
const iR = 80; // Inner Radius
const oR = 180; // Outer Radius

const needle = (value, data, cx, cy, iR, oR, color) => {
  let total = 0;
  data.forEach((v) => {
    total += v.value;
  });
  const ang = 180.0 * (1 - value / total);
  const length = (iR + 2 * oR) / 3;
  const sin = Math.sin(-RADIAN * ang);
  const cos = Math.cos(-RADIAN * ang);
  const r = 10; 
  const x0 = cx;
  const y0 = cy;
  const xba = x0 + r * sin;
  const yba = y0 - r * cos;
  const xbb = x0 - r * sin;
  const ybb = y0 + r * cos;
  const xp = x0 + length * cos;
  const yp = y0 + length * sin;

  return [
    <circle key="needle-circle" cx={x0} cy={y0} r={r} fill={color} stroke="none" />,
    <path key="needle-path" d={`M${xba} ${yba}L${xbb} ${ybb} L${xp} ${yp} L${xba} ${yba}`} stroke="#none" fill={color} />,
  ];
};

export default class DassMulticlassChart extends PureComponent {
  render() {
    const { severityLevel } = this.props;
    const value = (severityLevel / 5) * 180 + 18;

    return (
      <PieChart width={600} height={400}> {/* Increased size */}
        <Pie
          dataKey="value"
          startAngle={180}
          endAngle={0}
          data={data}
          cx={cx}
          cy={cy}
          innerRadius={iR}
          outerRadius={oR}
          fill="#8884d8"
          stroke="none"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
          <LabelList 
            dataKey="name" 
            position="inside" 
            style={{ fontSize: '12px', fontWeight: 'normal', fill: '#000' }} // Increased font size
            offset={20} // Adjusted offset for better spacing
          />
        </Pie>
        {needle(value, data, cx, cy, iR, oR, '#6C757D')}
      </PieChart>
    );
  }
}
