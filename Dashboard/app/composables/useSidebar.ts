export const useSidebar = () => {
  const isMobileOpen = useState<boolean>("sidebar-mobile-open", () => false);
  const isCollapsed = useState<boolean>("sidebar-collapsed", () => false);

  const toggleMobile = () => (isMobileOpen.value = !isMobileOpen.value);
  const closeMobile = () => (isMobileOpen.value = false);
  const toggleCollapse = () => (isCollapsed.value = !isCollapsed.value);

  return {
    isMobileOpen,
    isCollapsed,
    toggleMobile,
    closeMobile,
    toggleCollapse,
  };
};
