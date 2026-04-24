import type { TextareaHTMLAttributes } from "vue";

export interface TextareaProps
  extends /* @vue-ignore */ Omit<TextareaHTMLAttributes, "style"> {
  /**
   * The value of the textarea
   */
  modelValue?: string | number;

  /**
   *
   * @default 3
   */
  rows?: string | number;

  /**
   *
   * @default 'vertical'
   */
  resize?: "none" | "both" | "horizontal" | "vertical";

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

  disabled?: boolean;

  readonly?: boolean;

  required?: boolean;

  loading?: boolean;

  /**
   * Full width
   */
  block?: boolean;

  /**
   * ID attribute
   */
  id?: string;
}
