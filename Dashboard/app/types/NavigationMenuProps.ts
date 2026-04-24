import type { HTMLAttributes } from "vue";

export interface NavigationMenuProps extends /* @vue-ignore */ HTMLAttributes {
  modelValue?: string;
  defaultValue?: string;

  /**
   *
   * @default true
   */
  viewport?: boolean;

  /**
   *
   * @default 'horizontal'
   */
  orientation?: "horizontal" | "vertical";
}

export interface NavigationMenuListProps
  extends /* @vue-ignore */ HTMLAttributes {
  /**
   * @default 'center'
   */
  align?: "left" | "center" | "right";
}

export interface NavigationMenuItemProps
  extends /* @vue-ignore */ HTMLAttributes {
  value?: string;
}

export interface NavigationMenuTriggerProps
  extends /* @vue-ignore */ HTMLAttributes {
  disabled?: boolean;
}

export interface NavigationMenuContentProps
  extends /* @vue-ignore */ HTMLAttributes {
  forceMount?: boolean;
}

export interface NavigationMenuLinkProps
  extends /* @vue-ignore */ HTMLAttributes {
  active?: boolean;

  /**
   * Render as child component
   */
  asChild?: boolean;
  href?: string;
  target?: string;
}
