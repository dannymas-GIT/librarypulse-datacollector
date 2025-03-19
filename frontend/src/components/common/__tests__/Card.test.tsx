/** @jest-environment jsdom */
import { render, screen } from '@testing-library/react';
import Card from '../Card';

describe('Card', () => {
  it('renders children correctly', () => {
    render(
      <Card>
        <div>Test Content</div>
      </Card>
    );
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <Card className="custom-class">
        <div>Test Content</div>
      </Card>
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });
}); 