import type { ButtonHTMLAttributes } from "vue";

// We use @vue-ignore to ignore the Vue specific typescript errors
export interface ButtonProps extends /* @vue-ignore */ ButtonHTMLAttributes {
  color?: "primary" | "secondary" | "accent" | "danger" | "success" | "warning";

  variant?: "solid" | "outline" | "ghost" | "link";
  /**
   * Button size
   * @default 'md'
   */
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  /**
   * HTML button type
   * @default 'button'
   */
  type?: "button" | "submit" | "reset";
  /**
   * Disabled state
   */
  disabled?: boolean;
  /**
   * Loading state
   */
  loading?: boolean;
  /**
   * Full width button
   */
  block?: boolean;
  /**
   * Rounded corners
   */
  rounded?: "none" | "sm" | "md" | "lg" | "full";
  /**
   * Icon on the left
   */
  iconLeft?: string;
  /**
   * Icon on the right
   */
  iconRight?: string;
}
