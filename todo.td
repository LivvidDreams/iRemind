# TODO.td
## I hope I get to this

- File_handling:
    - Write out `processed_messages` to individual files in a temporary folder.
        - If marked as incomplete, read in the data to schedule the message for the future.
        - If marked complete, ensure it is not processed again when polling the database.

- In_Message replies:
    - Instead of only replying in the same chat, reply to the actual message if possible (so the reminder points back to the time it was sent).
        - If not possible, find the previous message sent in the chat and send a copy as the reminder message.
