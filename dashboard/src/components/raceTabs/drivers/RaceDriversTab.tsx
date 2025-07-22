import { useShowContext } from "react-admin";
import { useRaceDriverSummary } from "../../../hooks/useRaceDriverSummary";

export const RaceDriversTab = () => {
  const { record } = useShowContext();
  const { data, loading } = useRaceDriverSummary(record?.id);

  if (loading || !data) return <div>Loading...</div>;

  return (
    <div style={{ padding: "1rem" }}>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", flexWrap: "wrap" }}>
        <div style={{ flex: 1, minWidth: 220, border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
          <h3 style={{ marginBottom: "0.5rem" }}>Race Winner</h3>
          <p style={{ margin: 0 }}>{data.race_winner.team}</p>
          <p style={{ margin: 0 }}>{data.race_winner.driver}</p>
          <p style={{ color: "#666" }}>{data.race_winner.time}</p>
        </div>

        <div style={{ flex: 1, minWidth: 220, border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
          <h3 style={{ marginBottom: "0.5rem" }}>Pole Position</h3>
          <p style={{ margin: 0 }}>{data.pole_position.team}</p>
          <p style={{ margin: 0 }}>{data.pole_position.driver}</p>
          <p style={{ color: "#666" }}>{data.pole_position.time}</p>
        </div>

        <div style={{ flex: 1, minWidth: 220, border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
          <h3 style={{ marginBottom: "0.5rem" }}>Fastest Lap</h3>
          <p style={{ margin: 0 }}>{data.fastest_lap.team}</p>
          <p style={{ margin: 0 }}>{data.fastest_lap.driver}</p>
          <p style={{ color: "#666" }}>
            Lap {data.fastest_lap.lap} – {data.fastest_lap.time}
          </p>
        </div>
      </div>

      <h3>Race Results</h3>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
          <thead>
            <tr style={{ backgroundColor: "#f5f5f5", textAlign: "left" }}>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Pos.</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Driver</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Team</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Time</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Gap</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Interval</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Points</th>
              <th style={{ padding: "8px", borderBottom: "1px solid #ddd" }}>Laps</th>
            </tr>
          </thead>
          <tbody>
            {data.results.map((r: any, i: number) => (
              <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
                <td style={{ padding: "8px" }}>{r.position !== "\\N" ? r.position : "—"}</td>
                <td style={{ padding: "8px" }}>{r.driver}</td>
                <td style={{ padding: "8px" }}>{r.team}</td>
                <td style={{ padding: "8px" }}>{r.time !== "\\N" ? r.time : "—"}</td>
                <td style={{ padding: "8px" }}>{r.gap || "—"}</td>
                <td style={{ padding: "8px" }}>{r.interval || "—"}</td>
                <td style={{ padding: "8px" }}>{r.points}</td>
                <td style={{ padding: "8px" }}>{r.laps}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
