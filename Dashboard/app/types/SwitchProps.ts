import type { InputHTMLAttributes } from "vue";

export interface SwitchProps extends /* @vue-ignore */ InputHTMLAttributes {
  /**
   * Control the switch state
   */
  modelValue?: boolean;

  /**
   *
   * @default 'primary'
   */
  color?: "primary" | "secondary" | "accent" | "success" | "danger";
  class?: string;

  /**
   *
   * @default 'md'
   */
  size?: "sm" | "md" | "lg";

  /**
   *
   * @default false
   */
  disabled?: boolean;

  /**
   * Label text to display next to the switch
   */
  label?: string;

  /**
   * @default 'right'
   */
  labelPosition?: "left" | "right";

  /**
   * @default false
   */
  required?: boolean;
  name?: string;
  id?: string;
}
