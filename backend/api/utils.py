class ApiUtils:
    # Util functions
    @staticmethod
    def create_err_msg(err_code: int, text: str, json: dict = {}) -> str:
        return ApiUtils.create_msg("error", err_code, text, json)

    @staticmethod
    def create_success_msg(text, json: dict = {}) -> str:
        return ApiUtils.create_msg("success", 1, text, json)

    @staticmethod
    def create_msg(category: str, err_code: int, text: str, json: dict = {}) -> str:
        msg = {
            f"{category}": err_code,
            "text": text
        }
        msg.update(json)
        return msg