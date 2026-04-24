export const INTERNAL_AUTH_COOKIE = "hydralis_auth";
export const INTERNAL_AUTH_USERNAME = "hydralis";
export const INTERNAL_AUTH_PASSWORD = "bere1234@";
export const INTERNAL_AUTH_ROUTE = "/auth";

export const hasValidInternalSession = (sessionValue?: string | null) => {
  return sessionValue === INTERNAL_AUTH_USERNAME;
};

export const isValidInternalCredentials = (
  username: string,
  password: string,
) => {
  return (
    username.trim() === INTERNAL_AUTH_USERNAME &&
    password === INTERNAL_AUTH_PASSWORD
  );
};

export const sanitizeRedirectPath = (path: unknown) => {
  if (typeof path !== "string" || !path.startsWith("/")) {
    return "/";
  }

  if (path === INTERNAL_AUTH_ROUTE) {
    return "/";
  }

  return path;
};
