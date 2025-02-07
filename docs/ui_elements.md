
# UI Elements Configuration Guide

## Basic Structure

The UI elements configuration file is a JSON file that defines the structure and behavior of various UI elements such as buttons, modals, and embeds. This file is used to dynamically create and manage these elements within your Discord bot.

### Example Structure

```json
{
    "guild_id": {
        "element_name": {
            "persistent": true,
            "embeds": [
                {
                    "title": "Embed Title",
                    "description": "Embed Description",
                    "color": 123456,
                    "fields": [
                        {
                            "name": "Field Name",
                            "value": "Field Value",
                            "inline": true
                        }
                    ]
                }
            ],
            "components": [
                {
                    "type": "button",
                    "custom_id": "button_id",
                    "label": "Button Label",
                    "style": 1,
                    "disabled": false
                }
            ],
            "actions": [
                {
                    "custom_id": "button_id",
                    "type": "message",
                    "message": "Button clicked!"
                }
            ]
        }
    }
}
```

### Fields Description

- `guild_id`: The ID of the guild (server) where the UI elements will be used.
- `element_name`: A unique name for the UI element.
- `persistent`: A boolean indicating whether the UI element should persist across bot restarts.
- `embeds`: A list of embed objects to be included in the UI element.
  - `title`: The title of the embed.
  - `description`: The description of the embed.
  - `color`: The color of the embed (in decimal format).
  - `fields`: A list of field objects to be included in the embed.
    - `name`: The name of the field.
    - `value`: The value of the field.
    - `inline`: A boolean indicating whether the field should be displayed inline.
- `components`: A list of component objects to be included in the UI element.
  - `type`: The type of the component (e.g., `button`).
  - `custom_id`: A unique ID for the component.
  - `label`: The label of the component.
  - `style`: The style of the component (e.g., 1 for primary button).
  - `disabled`: A boolean indicating whether the component should be disabled.
- `actions`: A list of action objects to define the behavior of the components.
  - `custom_id`: The custom ID of the component that triggers the action.
  - `type`: The type of the action (e.g., `message`).
  - `message`: The message to be sent when the action is triggered (for `message` type actions).

## Usage

To use the UI elements configuration file, place it in the appropriate directory (e.g., `./data/ui_elements.json`) and ensure that your bot is set up to load and process this file. The `UIFetcher` class in the provided code is responsible for loading and managing the UI elements based on this configuration.