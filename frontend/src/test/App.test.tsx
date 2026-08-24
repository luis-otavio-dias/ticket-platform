import { render, screen } from '@testing-library/react'
import App from '../App'

test("render App", () => {
  render(<App />)
  const button = screen.getByRole('button')
  expect(button).toBeInTheDocument()
})
