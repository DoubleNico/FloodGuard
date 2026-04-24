export type PopoverPlacement =
  | "top"
  | "bottom"
  | "left"
  | "right"
  | "top-start"
  | "top-end"
  | "bottom-start"
  | "bottom-end"
  | "left-start"
  | "left-end"
  | "right-start"
  | "right-end";

export interface PopoverProps {
  modelValue?: boolean;
  placement?: PopoverPlacement;
  offset?: number;
  disabled?: boolean;
  trigger?: "click" | "hover";
  hoverDelay?: number;
  block?: boolean;
}
