# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A simple notes application built with Python's tkinter GUI library. Notes are persisted as a JSON array of strings.

## Running the Application

```bash
python notes_app.py
```

## Project Structure

- `notes_app.py` - Main application containing the NotesApp class with tkinter GUI widgets
- `notes.json` - Data file storing notes as a JSON array of strings

## Architecture

Single-file application using a class-based structure:
- `NotesApp` class handles all UI components and data operations
- Data is loaded/saved to `notes.json` using Python's json module
- Tkinter widgets include: Label, Entry, Buttons, Listbox with Scrollbar
- Default fallback notes: `["youtube reminder"]` when data file is missing or corrupted
