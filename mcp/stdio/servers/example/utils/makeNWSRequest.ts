// Helper function for making NWS API requests
import { z } from "zod";

export const AlertFeatureSchema = z.object({
  properties: z.object({
    event: z.string().optional(),
    areaDesc: z.string().optional(),
    severity: z.string().optional(),
    status: z.string().optional(),
    headline: z.string().optional(),
  }),
});

export const AlertsResponseSchema = z.object({
  features: z.array(AlertFeatureSchema),
});

export const ForecastPeriodSchema = z.object({
  name: z.string().optional(),
  temperature: z.number().optional(),
  temperatureUnit: z.string().optional(),
  windSpeed: z.string().optional(),
  windDirection: z.string().optional(),
  shortForecast: z.string().optional(),
});

export const PointsResponseSchema = z.object({
  properties: z.object({
    forecast: z.string().optional(),
  }),
});

export const ForecastResponseSchema = z.object({
  properties: z.object({
    periods: z.array(ForecastPeriodSchema),
  }),
});

const USER_AGENT = "weather-app/1.0";
export async function makeNWSRequest<T>(url: string): Promise<T | null> {
  const headers = {
    "User-Agent": USER_AGENT,
    Accept: "application/geo+json",
  };

  try {
    const response = await fetch(url, { headers });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    console.error("Error making NWS request:", error);
    return null;
  }
}



// Format alert data
export function formatAlert(
  feature: z.infer<typeof AlertFeatureSchema>
): string {
  const props = feature.properties;
  return [
    `Event: ${props.event || "Unknown"}`,
    `Area: ${props.areaDesc || "Unknown"}`,
    `Severity: ${props.severity || "Unknown"}`,
    `Status: ${props.status || "Unknown"}`,
    `Headline: ${props.headline || "No headline"}`,
    "---",
  ].join("\n");
}

