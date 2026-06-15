# Project Demo Video

This folder contains details and the transcription for the project's demo video.

## Video Link

🎥 **Watch the Demo Video:** [Loom Video - Network Configuration Difference Reviewer with AI](https://www.loom.com/share/9af403bdb6e64d0992ae23556a04d1bb)

---

## Video Overview

In this video, the project team (Geetanjali and teammates) presents the **Network Configuration Difference Reviewer with AI** prototype. The presentation details the problem statement, how the python-based diff and rule checking works, the structured JSON integration with Google Gemini, and the final approval package export features.

### Chapters
* **00:00** Project problem and goal
* **01:34** How file comparison works
* **03:45** Rule checks for risky changes
* **05:46** Approval pack and future plans

---

## Full Video Transcript

* **[00:00]** Hi everyone, I am Geetanjali. Today we are presenting our project called Network Configuration Difference Reviewer.
* **[00:10]** In real companies, network teams often change router or firewall settings. Right now, these changes are usually uploaded over email, without any proper check.
* **[00:20]** This is risky, because a small mistake in your configure file can open up the whole network to attacks. Let's take a small example.
* **[00:29]** Imagine someone changes your firewall network settings. And now it allows traffic from anywhere to anywhere. If nobody checks this properly, it could stay unnoticed for days or weeks.
* **[00:41]** And during that time, the network gets exposed. Our project solved this problem. It's a small tool that compares an old configuration file and a new configuration file, finds out what changed, checks if any change is risky, and then uses AI to explain everything in simple language.
* **[00:59]** At the end, it creates a report that the team can attach to their approval ticket. Our project is built using Python, and the interface is made with Streamlit, which makes it easy to use directly from your browser.
* **[01:13]** For comparing files, we use Python's built-in `difflib` library. For AI, we use Google's Gemini models. The Gemini API is free to use.
* **[01:23]** And for generating PDF reports, we use a library called `fpdf2`. It will be continued by my teammate. Now let me explain how our tool actually works.
* **[01:33]** First, the user uploads two files, the one from old configuration and the new configuration. We have also added sample files so you don't have to create your own.
* **[01:42]** Our Python code uses a tool called `difflib` to compare both files line by line and shows exactly what was added, removed, or changed.
* **[01:51]** After that, through the Python code, we run some simple rule-based checks. These checks look for risky patterns like:
  * If an access rule was made too open (for example, changing it to `permit ip any any`).
  * If a new network route was added or removed.
  * If any BGP peer settings changed (such as remote AS number, description, or password).
  * If the SNMP community string was changed from read-only (RO) to read-write (RW).
* **[02:10]** In our sample files, all four of these risky changes are present. So our tool can detect all of them. Let me walk you through each one.
* **[02:20]** In the old configuration, the access list allows only simple traffic (web traffic, secure web traffic, and DNS) and blocks everything else.
* **[02:35]** In the new configuration, someone added a line that allows all traffic, both in and out. This is a major risk because it removes the protection that the access list was providing.
* **[02:47]** Next, in the old configuration, there were two routes: one to a local network, and one default route. In the new configuration, a brand new route was added pointing to a different network.
* **[02:59]** This means traffic can now go to a place it couldn't go before. So, we need to check if that's intended.
* **[03:06]** For BGP, the old configuration had a peer with AS number 65666. In the new configuration, this peer's AS number changed to 65009 and the description changed to `Peer ISP B Backup`.
* **[03:25]** This could mean we are now trusting a completely different external network as our peer.
* **[03:29]** Lastly, the SNMP community string changed from Read-Only to Read-Write. This is risky because Read-Write access means someone could not just view the device settings, but also change them remotely using SNMP.
* **[03:45]** Now, the next process will be continued by my teammate. This is the AI part of our project: After the rule-based check is done, we send the diff and the flagged changes to the Google Gemini AI model.
* **[04:06]** We ask the AI to act like a senior network / security engineer. One of the important things about our AI integration is that we don't just get a paragraph of text back; we specifically ask the AI to reply in a fixed JSON format.
* **[04:22]** This includes:
  * Overall summary
  * Risk level (low, medium, high)
  * A structured list of findings containing:
    * Risk type
    * Actual configuration line
    * Easy explanation
    * Risk level
    * Recommended action for reviewer
  * Assumptions or limitations
* **[04:41]** This structured format is useful for our app to present the data, for example, to build tables, display risk levels, and generate reports without needing to manually read through long, unstructured text.
* **[04:55]** For example, for the SNMP changes, the AI might say the community string was changed from read-only to write, meaning anyone with this community string can modify the device configuration, which is high-risk and should be reviewed immediately.
* **[05:12]** For the BGP change, it might explain the remote AS number and description changes, indicating the network peer has been modified.
* **[05:20]** We also added validation: if the AI's response doesn't match the expected JSON format, our app doesn't break. Instead, it shows a friendly error message, and the diff and rule-based results still work fine.
* **[05:31]** Finally, let me show you the output and wrap-up.
* **[05:46]** Once everything is processed, our tool creates a final approval pack. This report is organized into clear sections:
  1. Summary of all changes
  2. The full diff (so reviewers can see exactly what changed line by line)
  3. Rule-based flags in a simple list
  4. The AI's review and findings
  5. An approval checklist where reviewers can confirm they checked everything before approving the change
* **[06:22]** From there, the user can download the approval pack. The pack contains:
  * A Markdown file (`.md`)
  * A PDF report (`.pdf`)
  * A CSV file containing just the flagged risky changes (`.csv`)
* **[06:33]** In the future, we plan to add support for other types of devices like Juniper or Palo Alto, since right now our rule-based checks are designed mainly for Cisco-style configurations. We also want to connect this tool directly to a ticketing system, so the approval pack can be attached automatically when a change request is created.
* **[06:57]** To sum up, our tool turns a risky, manual, email-based approval process into a quicker, clearer, and AI-assisted review, helping teams catch mistakes before they cause real problems.
* **[07:14]** Thank you for listening, and we are happy to answer any questions.
