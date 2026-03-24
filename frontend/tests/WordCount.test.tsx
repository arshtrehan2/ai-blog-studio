import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { WordCount } from "../components/editor/WordCount";

describe("WordCount", () => {
  it("shows 0 words for empty content", () => {
    render(<WordCount content="" />);
    expect(screen.getByText(/0 words/i)).toBeTruthy();
  });

  it("counts words correctly", () => {
    render(<WordCount content="Hello world this is five" />);
    expect(screen.getByText(/5 words/i)).toBeTruthy();
  });

  it("shows character count", () => {
    render(<WordCount content="abc" />);
    expect(screen.getByText(/3 chars/i)).toBeTruthy();
  });
});
