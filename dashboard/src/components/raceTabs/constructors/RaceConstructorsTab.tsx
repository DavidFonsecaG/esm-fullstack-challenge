import { useShowContext } from "react-admin";
import { useRaceConstructorSummary } from "../../../hooks/useRaceConstructorSummary";
import Plot from "react-plotly.js";


export const RaceConstructorsTab = () => {
  const { record } = useShowContext();
  const { data, loading } = useRaceConstructorSummary(record?.id);

  if (loading || !data) return <div>Loading...</div>;

  return (
    <div style={{ padding: "1rem" }}>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", flexWrap: "wrap" }}>
        <div style={{ flex: 1, minWidth: 220, border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
          <h3 style={{ marginBottom: "0.5rem" }}>Best Finishing Constructor</h3>
          <p style={{ margin: 0 }}>{data.best_finisher?.team}</p>
          <p style={{ color: "#666" }}>Pos. {data.best_finisher?.position}</p>
        </div>

        <div style={{ flex: 1, minWidth: 220, border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
          <h3 style={{ marginBottom: "0.5rem" }}>Constructor with Most Points</h3>
          <p style={{ margin: 0 }}>{data.most_points?.team}</p>
          <p style={{ color: "#666" }}>{data.most_points?.points} pts</p>
        </div>
      </div>

      <h3>Constructor Results</h3>
      <div style={{ overflowX: "auto", marginBottom: "2rem" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
          <thead>
            <tr style={{ backgroundColor: "#f5f5f5", textAlign: "left" }}>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Team</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Drivers</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Best Pos.</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Avg Pos.</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Points</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Laps</th>
            </tr>
          </thead>
          <tbody>
            {data.results.map((c: any, i: number) => (
              <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
                <td style={{ padding: "8px" }}>{c.team}</td>
                <td style={{ padding: "8px" }}>{Array.isArray(c.drivers) ? c.drivers.join(", ") : c.drivers}</td>
                <td style={{ padding: "8px" }}>{c.best_position}</td>
                <td style={{ padding: "8px" }}>{c.avg_position.toFixed(2)}</td>
                <td style={{ padding: "8px" }}>{c.total_points}</td>
                <td style={{ padding: "8px" }}>{c.laps_completed}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ border: "1px solid #ccc", borderRadius: "8px", padding: "1rem", marginTop: "1rem" }}>
        <h3>Driver Points per Constructor</h3>
        <Plot
          style={{ width: "100%" }}
          useResizeHandler
          data={Object.values(
            data.driver_points.reduce((acc: any, { constructor, driver, points }: any) => {
              if (!acc[constructor]) {
                acc[constructor] = { x: [], y: [], type: "bar", name: constructor };
              }
              acc[constructor].x.push(driver);
              acc[constructor].y.push(points);
              return acc;
            }, {})
          )}
          layout={{ height: 300, barmode: "group", margin: { t: 10 } }}
        />
      </div>

      <div style={{ border: "1px solid #ccc", borderRadius: "8px", padding: "1rem", marginTop: "1rem" }}>
        <h3>Constructor Position Evolution</h3>
        <Plot
          style={{ width: "100%" }}
          useResizeHandler={true}
          data={Object.values(
            data.position_evolution.reduce((acc: any, { team, lap, position }: any) => {
              if (!acc[team]) {
                acc[team] = {
                  x: [],
                  y: [],
                  text: [],
                  type: "scatter",
                  mode: "lines+markers",
                  marker: { size: 4 },
                  name: team,
                  hovertemplate: "Lap %{x}<br>Pos %{y}<extra>%{text}</extra>"
                };
              }
              acc[team].x.push(lap);
              acc[team].y.push(position);
              acc[team].text.push(team);
              return acc;
            }, {})
          )}
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
  );
};
