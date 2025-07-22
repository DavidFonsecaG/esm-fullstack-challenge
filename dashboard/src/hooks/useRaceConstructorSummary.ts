import { useEffect, useState } from "react";
import { API_BASE_URL } from "../utils/common";

export const useRaceConstructorSummary = (raceId: number | string | undefined) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!raceId) return;

    const fetchSummary = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/races/race_constructor_summary/${raceId}`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error("Failed to load constructor summary", err);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, [raceId]);

  return { data, loading };
};