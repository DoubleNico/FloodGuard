import type { InputHTMLAttributes } from "vue";
import type { CustomSelectOption } from "./CustomSelectProps";

export interface InputProps
  extends /* @vue-ignore */ Omit<InputHTMLAttributes, "size"> {
  modelValue?: string | Date | number | null;
  type?:
    | "text"
    | "email"
    | "password"
    | "number"
    | "tel"
    | "url"
    | "search"
    | "date"
    | "time"
    | "datetime-local"
    | "month"
    | "week"
    | "color"
    | "custom-color"
    | "custom-date"
    | "file"
    | "range"
    | "hidden";
  size?: "xs" | "sm" | "base" | "md" | "lg" | "xl";
  color?: "primary" | "secondary" | "accent" | "success" | "danger";
  disabled?: boolean;
  readonly?: boolean;
  required?: boolean;
  placeholder?: string;
  label?: string;
  hint?: string;
  error?: string;
  iconLeft?: string;
  iconRight?: string;
  loading?: boolean;
  autofocus?: boolean;
  clearable?: boolean;
  block?: boolean;
  name?: string;
  id?: string;
  autocomplete?: string;
  min?: string | number;
  max?: string | number;
  step?: string | number;
  enableTime?: boolean;
  pattern?: string;
  maxlength?: number;
  minlength?: number;
  inputmode?:
    | "none"
    | "text"
    | "decimal"
    | "numeric"
    | "tel"
    | "search"
    | "email"
    | "url";
  prefixValue?: string | number;
  prefixOptions?: CustomSelectOption[];
  prefixSearchable?: boolean;
}
