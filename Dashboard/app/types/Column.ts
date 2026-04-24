export interface Column {
  key: string;
  label: string;
  width?: string;
  align?: "left" | "center" | "right";
  sortable?: boolean;
  sortOrder?: string[];
  sortLabels?: { asc: string; desc: string };
}
