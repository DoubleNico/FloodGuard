import type { HTMLAttributes } from "vue";

export interface MobileNavigationMenuSectionProps {
  title?: string;
}

export interface MobileNavigationMenuLinkProps {
  href?: string;
  inDropdown?: boolean;
}

export interface MobileNavigationMenuDropdownProps {
  title: string;
  defaultOpen?: boolean;
}

export interface MobileNavigationMenuProps
  extends /* @vue-ignore */ HTMLAttributes {
  /**
   * Is menu open or not
   */
  modelValue?: boolean;

  /**
   *
   * @default 'right'
   */
  buttonPosition?: "left" | "right";
}
