export interface GridProps {
  cols?: number | string;

  rows?: number | string;

  gap?: number | string;

  gapX?: number | string;

  gapY?: number | string;

  /**
   *
   * @default 'row'
   */
  flow?: "row" | "col" | "row-dense" | "col-dense";

  items?: "start" | "center" | "end" | "stretch" | "baseline";

  justify?: "start" | "center" | "end" | "stretch";

  content?: "start" | "center" | "end" | "between" | "around" | "evenly";

  as?: string;
}
