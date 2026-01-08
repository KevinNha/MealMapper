import React from 'react';
import { render } from '@testing-library/react-native';
import UiMobile from './ui-mobile';

describe('UiMobile', () => {
  it('should render successfully', () => {
    const { root } = render(<UiMobile />);
    expect(root).toBeTruthy();
  });
});
