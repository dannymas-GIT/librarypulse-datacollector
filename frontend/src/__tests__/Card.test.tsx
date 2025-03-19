import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Card } from '../components/ui/Card';

describe('Card Component', () => {
  it('renders with children content', () => {
    render(
      <Card>
        <div>Test Content</div>
      </Card>
    );
    
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('applies className correctly', () => {
    const { container } = render(
      <Card className="test-class">
        <div>Test Content</div>
      </Card>
    );
    
    const cardElement = container.firstChild;
    expect(cardElement).toHaveClass('test-class');
  });
}); 