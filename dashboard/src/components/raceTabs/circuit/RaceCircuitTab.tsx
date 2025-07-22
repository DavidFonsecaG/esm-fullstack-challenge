import { useShowContext, ReferenceField } from "react-admin";
import { useRaceCircuitSummary } from "../../../hooks/useRaceCircuitSummary";
import Plot from "react-plotly.js";
import { WikiImage } from "./WikiImage";

export const RaceCircuitTab = () => {
  const { record } = useShowContext();
  const { data, loading } = useRaceCircuitSummary(record?.id);

  if (loading || !data) return <div>Loading...</div>;

  const allLapTimes = data.pace_evolution.map((d: any) => d.milliseconds);
  const minMs = Math.min(...allLapTimes);
  const maxMs = Math.max(...allLapTimes);

  const formatMsToMinSec = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = ((ms % 60000) / 1000).toFixed(3).padStart(6, "0");
    return `${minutes}:${seconds}`;
  };

  const step = Math.round((maxMs - minMs) / 9);
  const tickvals = Array.from({ length: 10 }, (_, i) => minMs + i * step);
  const ticktext = tickvals.map(formatMsToMinSec);

  return (
    <div style={{ padding: "1rem" }}>
      <h2>
        {data.race_name} - {data.location} {data.year} - <ReferenceField source="circuit_id" reference="circuits" />
      </h2>
      <WikiImage titleField="name" />
      <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
        <div style={{ flex: 1, border: "1px solid #ccc", borderRadius: "8px", paddingTop: "1rem" }}>
          <h3 style={{ marginLeft: "1rem" }}>Top 20 Fastest Laps</h3>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
            <thead>
              <tr style={{ backgroundColor: "#f5f5f5", textAlign: "left" }}>
                <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Pos.</th>
                <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Driver</th>
                <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Lap</th>
                <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Time (sec)</th>
              </tr>
            </thead>
            <tbody>
              {data.top_fastest_laps.map((lap: any, idx: number) => (
                <tr key={idx} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={{ padding: "8px" }}>{lap.position}</td>
                  <td style={{ padding: "8px" }}>{lap.driver}</td>
                  <td style={{ padding: "8px" }}>{lap.lap}</td>
                  <td style={{ padding: "8px" }}>{formatMsToMinSec(lap.milliseconds)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ flex: 2, display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
            <h3>Race Pace Evolution</h3>
            <Plot
              style={{ width: "100%" }}
              useResizeHandler={true}            
              data={Object.values(
                data.pace_evolution.reduce((acc: any, { driver, lap, milliseconds }: any) => {
                  if (!acc[driver]) {
                    acc[driver] = { x: [], y: [], text: [], type: "scatter", mode: "lines+markers", name: driver, marker: { size: 4 }, hovertemplate: "Lap %{x}<br>%{text.time}<extra>%{text.driver}</extra>" };
                  }
                  acc[driver].x.push(lap);
                  acc[driver].y.push(milliseconds);
                  acc[driver].text.push({driver: driver, time:formatMsToMinSec(milliseconds)});
                  return acc;
                }, {})
              )}
              layout={{
                height: 400,
                xaxis: { title: "Lap" },
                yaxis: { title: "Lap Time (min:sec)", tickvals: tickvals, ticktext: ticktext },
                margin: { t: 10 },
                showlegend: false
              }}
            />
          </div>
          <div style={{ border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
            <h3>Race Pace Box Plot</h3>
            <Plot
              style={{ width: "100%" }}
              useResizeHandler={true}            
              data={
                Object.values(
                  data.pace_evolution.reduce((acc: any, { driver, milliseconds }: any) => {
                    if (!acc[driver]) {
                      acc[driver] = {
                        y: [],
                        type: "box",
                        name: driver,
                        boxpoints: false,
                      };
                    }
                    acc[driver].y.push(milliseconds);
                    return acc;
                  }, {})
                )
              }
              layout={{
                height: 400,
                yaxis: { title: "Lap Time (min:sec)", tickvals: tickvals, ticktext: ticktext },
                margin: { t: 10 },
                showlegend: false
              }}
            />
          </div>
          <div style={{ border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
            <h3>Position Evolution</h3>
            <Plot
              style={{ width: "100%" }}
              useResizeHandler={true}
              data={
                Object.values(
                  data.position_evolution.reduce((acc: any, { driver, lap, position }: any) => {
                    if (!acc[driver]) {
                      acc[driver] = {
                        x: [],
                        y: [],
                        text: [],
                        type: "scatter",
                        mode: "lines+markers",
                        marker: { size: 4 },
                        name: driver,
                        hovertemplate: "Lap %{x}<br>Pos %{y}<extra>%{text}</extra>"
                      };
                    }
                    acc[driver].x.push(lap);
                    acc[driver].y.push(position);
                    acc[driver].text.push(driver);
                    return acc;
                  }, {})
                )
              }
              layout={{
                height: 400,
                xaxis: { title: "Lap" },
                yaxis: { title: "Position", autorange: "reversed" },
                margin: { t: 10 },
                showlegend: false
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
