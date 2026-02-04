## secure_eo_pipeline/utils/security.py
L1: Comment describing `os` import.
L2: Imports `os` for file operations.
L3: Comment describing `hashlib` import.
L4: Imports `hashlib` for SHA-256 hashing.
L5: Comment describing Fernet import.
L6: Imports `Fernet` for symmetric encryption.
L7: Comment describing config import.
L8: Imports `config` for key file path.
L9: Separator comment for module description.
L10: Comment describing purpose.
L11: Comment describing design rationale.
L12: Separator line.
L13: Defines `generate_key`.
L14: Starts docstring.
L15: Docstring line describing output.
L16: Blank line in docstring.
L17: Docstring rationale.
L18: Ends docstring.
L19: Comment describing key generation.
L20: Generates a new Fernet key.
L21: Blank line before writing.
L22: Comment describing file write.
L23: Opens key file for binary writing.
L24: Writes key bytes to disk.
L25: Blank line before permissions.
L26: Comment describing permission tightening.
L27: Attempts to set file permissions to owner-only.
L28: Starts exception handling.
L29: Ignores permission errors on unsupported platforms.
L30: Blank line before user message.
L31: Comment describing notification.
L32: Prints success message.
L33: Blank line before `load_key`.
L34: Defines `load_key`.
L35: Starts docstring.
L36: Docstring line describing behavior.
L37: Blank line in docstring.
L38: Docstring return description.
L39: Blank line in docstring.
L40: Docstring describing secure default.
L41: Ends docstring.
L42: Comment describing existence check.
L43: Checks if key file exists.
L44: Comment describing creation.
L45: Generates a new key if missing.
L46: Blank line before file read.
L47: Starts try block for file read.
L48: Comment describing read.
L49: Opens key file for binary read.
L50: Returns file contents.
L51: Ends try block.
L52: Starts exception handling.
L53: Comment describing fatal error.
L54: Prints error message.
L55: Raises the exception to stop execution.
L56: Blank line before `encrypt_file`.
L57: Defines `encrypt_file`.
L58: Starts docstring.
L59: Docstring line describing behavior.
L60: Blank line in docstring.
L61: Docstring argument description.
L62: Blank line in docstring.
L63: Docstring describing flow.
L64: Ends docstring.
L65: Comment describing key retrieval.
L66: Loads the key.
L67: Blank line before Fernet object.
L68: Comment describing Fernet initialization.
L69: Creates a Fernet instance.
L70: Blank line before encryption.
L71: Starts try block.
L72: Comment describing file read.
L73: Opens file for reading.
L74: Reads all file data.
L75: Blank line before encryption.
L76: Comment describing encryption.
L77: Encrypts the data.
L78: Blank line before write back.
L79: Comment describing overwrite.
L80: Opens file for binary write.
L81: Writes encrypted data.
L82: Ends try block.
L83: Handles missing file.
L84: Prints a not found error.
L85: Handles generic errors.
L86: Prints unexpected failure.
L87: Blank line before `decrypt_file`.
L88: Defines `decrypt_file`.
L89: Starts docstring.
L90: Docstring line describing behavior.
L91: Blank line in docstring.
L92: Docstring argument description.
L93: Blank line in docstring.
L94: Docstring describing authenticated decryption.
L95: Ends docstring.
L96: Comment describing key load.
L97: Loads the key.
L98: Blank line before Fernet object.
L99: Comment describing initialization.
L100: Creates a Fernet instance.
L101: Blank line before decryption.
L102: Starts try block.
L103: Comment describing encrypted read.
L104: Opens file for reading.
L105: Reads encrypted data.
L106: Blank line before decryption.
L107: Comment describing decryption.
L108: Decrypts the data.
L109: Blank line before overwrite.
L110: Comment describing write.
L111: Opens file for writing.
L112: Writes decrypted bytes.
L113: Ends try block.
L114: Handles decryption errors.
L115: Prints error message.
L116: Raises the exception to signal failure.
L117: Blank line before `calculate_hash`.
L118: Defines `calculate_hash`.
L119: Starts docstring.
L120: Docstring line describing behavior.
L121: Blank line in docstring.
L122: Docstring argument description.
L123: Blank line in docstring.
L124: Docstring describing SHA-256 rationale.
L125: Blank line in docstring.
L126: Docstring return description.
L127: Ends docstring.
L128: Comment describing hash initialization.
L129: Creates a SHA-256 hash object.
L130: Blank line before file read.
L131: Starts try block.
L132: Comment describing open.
L133: Opens the file in binary mode.
L134: Comment describing chunked reading.
L135: Iterates over 4096-byte blocks.
L136: Comment describing update.
L137: Updates hash with each chunk.
L138: Blank line before finalize.
L139: Comment describing digest.
L140: Returns the hex digest.
L141: Handles missing file.
L142: Prints missing file error.
L143: Returns None.