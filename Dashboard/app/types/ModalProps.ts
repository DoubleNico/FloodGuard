export interface ModalProps {
  modelValue: boolean;
  title?: string;
  persistent?: boolean;
  hideClose?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  panelClass?: string | string[];
}
