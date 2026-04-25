import {
  AUTH_TOKEN_COOKIE,
  INTERNAL_AUTH_ROUTE,
  hasValidInternalSession,
  sanitizeRedirectPath,
} from "~/utils/internalAuth";

export default defineNuxtRouteMiddleware((to) => {
  const tokenCookie = useCookie<string | null>(AUTH_TOKEN_COOKIE);
  const isAuthenticated = hasValidInternalSession(tokenCookie.value);
  const isAuthRoute =
    to.path === INTERNAL_AUTH_ROUTE ||
    to.path.startsWith(`${INTERNAL_AUTH_ROUTE}/`);

  if (!isAuthenticated && !isAuthRoute) {
    return navigateTo({
      path: INTERNAL_AUTH_ROUTE,
      query: {
        redirect: to.fullPath,
      },
    });
  }

  if (isAuthenticated && isAuthRoute) {
    return navigateTo(sanitizeRedirectPath(to.query.redirect));
  }
});
