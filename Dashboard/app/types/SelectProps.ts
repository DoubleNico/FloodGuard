import type { SelectHTMLAttributes } from "vue";

export interface SelectOption {
  label: string;
  value: string | number;
  disabled?: boolean;
}

export interface SelectProps
  extends /* @vue-ignore */ Omit<SelectHTMLAttributes, "size"> {
  /**
   * The selected value
   */
  modelValue?: string | number;

  /**
   * List of options
   * @see SelectOption
   */
  options?: (string | SelectOption)[];

  /**
   *
   * @default 'md'
   */
  size?: "sm" | "md" | "lg";

  /**
   *
   * @default 'primary'
   */
  color?: "primary" | "secondary" | "accent" | "success" | "danger";

  /**
   * Label text
   */
  label?: string;

  /**
   * Helper text
   */
  hint?: string;

  /**
   * Error message
   */
  error?: string;

  /**
   * Icon to display on the left
   */
  iconLeft?: string;

  /**
   *
   * @default false
   */
  disabled?: boolean;

  /**
   *
   * @default false
   */
  required?: boolean;

  /**
   *
   * @default false
   */
  loading?: boolean;

  /**
   *
   * @default false
   */
  block?: boolean;

  placeholder?: string;

  id?: string;
}
