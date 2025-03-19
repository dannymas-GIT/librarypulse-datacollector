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
  
  it('renders title and subtitle', () => {
    render(
      <Card title="Card Title" subtitle="Card Subtitle">
        <div>Test Content</div>
      </Card>
    );
    
    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card Subtitle')).toBeInTheDocument();
  });
  
  it('renders with footer', () => {
    render(
      <Card 
        footer={<div>Footer Content</div>}
      >
        <div>Test Content</div>
      </Card>
    );
    
    expect(screen.getByText('Footer Content')).toBeInTheDocument();
  });
}); 