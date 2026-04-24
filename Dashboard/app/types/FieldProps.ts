import type { HTMLAttributes } from "vue";

export interface FieldProps extends /* @vue-ignore */ HTMLAttributes {
  /**
   * Label text
   */
  label?: string;

  /**
   * Gives hint below field
   */
  hint?: string;

  /**
   * Gives error below field
   */
  error?: string;

  /**
   *
   * @default false
   */
  required?: boolean;

  id?: string;
}
