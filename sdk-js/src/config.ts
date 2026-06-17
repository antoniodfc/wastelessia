export interface Config {
  apiKey: string;
  endpoint: string;
}

let current: Config | null = null;

export interface ConfigureOptions {
  apiKey: string;
  endpoint?: string;
}

export function configure(options: ConfigureOptions): void {
  current = {
    apiKey: options.apiKey,
    endpoint: (options.endpoint ?? "https://api.wastelessia.com").replace(/\/+$/, ""),
  };
}

export function getConfig(): Config {
  if (current === null) {
    current = {
      apiKey: process.env.WASTELESSIA_API_KEY ?? "",
      endpoint: (process.env.WASTELESSIA_ENDPOINT ?? "https://api.wastelessia.com").replace(
        /\/+$/,
        "",
      ),
    };
  }
  return current;
}

/** Test helper: reset cached config so env vars are re-read. */
export function resetConfig(): void {
  current = null;
}
