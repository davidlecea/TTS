# Text to speech

`{
text: "text to be converted",
language: "en"      # es, en or ar for Spanish, English or Arabic
}`

How to test in shell:

`curl -i -H "Content-Type: application/json" -X POST -d '{"text":"Text to convert to audio", "language": "en"}' http://localhost:5000/generate_audio -o test.mp3`