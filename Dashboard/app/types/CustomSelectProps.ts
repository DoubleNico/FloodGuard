import type { HTMLAttributes } from "vue";

export interface CustomSelectOption {
  label: string;
  value: string | number;
  disabled?: boolean;
  icon?: string;
}

export interface CustomSelectProps extends /* @vue-ignore */ HTMLAttributes {
  modelValue?: string | number;

  /**
   * List of options
   * @see CustomSelectOption
   */
  options?: CustomSelectOption[];

  /**
   * The size of the select
   * @default 'md'
   */
  size?: "sm" | "md" | "lg";

  /**
   * The color scheme
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
   * Whether the select is disabled
   */
  disabled?: boolean;

  /**
   * Whether the field is required
   */
  required?: boolean;

  /**
   * Whether to show a loading spinner
   * @default false
   */
  loading?: boolean;

  /**
   * Full width
   * @default false
   */
  block?: boolean;

  /**
   * Placeholder text
   */
  placeholder?: string;

  /**
   * ID attribute
   */
  id?: string;

  /**
   * Enable search/filter functionality
   * @default false
   */
  searchable?: boolean;

  /**
   * Allow clearing the selection
   * @default false
   */
  clearable?: boolean;

  /**
   * Hide the scrollbar while allowing scroll
   * @default false
   */
  hideScrollbar?: boolean;
}
