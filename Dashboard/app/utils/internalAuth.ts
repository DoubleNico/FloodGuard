export const AUTH_TOKEN_COOKIE = "hydralis_token";
export const AUTH_USER_COOKIE = "hydralis_user";
export const INTERNAL_AUTH_ROUTE = "/auth";

export const hasValidInternalSession = (tokenValue?: string | null) => {
  return !!tokenValue && tokenValue.length > 0;
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
