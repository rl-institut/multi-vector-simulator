class economics:
    # todo check wheter this is the most recent version
    # - there were some project costs included wrongly,
    # and something with the replacement costs

    # annuity factor to calculate present value of cash flows
    def annuity_factor(self, project_life, wacc):
        """

        Parameters
        ----------
        project_life
        wacc

        Returns
        -------

        """
        # discount_rate was replaced here by wacc
        annuity_factor = 1 / wacc - 1 / (wacc * (1 + wacc) ** project_life)
        return annuity_factor

    # accounting factor to translate present value to annual cash flows
    def crf(self, project_life, wacc):
        """

        Parameters
        ----------
        project_life
        wacc

        Returns
        -------

        """
        crf = (wacc * (1 + wacc) ** project_life) / ((1 + wacc) ** project_life - 1)
        return crf

    def capex_from_investment(self, investment_t0, lifetime, project_life, wacc, tax):
        """

        Parameters
        ----------
        investment_t0
        lifetime
        project_life
        wacc
        tax

        Returns
        -------

        """
        # [quantity, investment, installation, weight, lifetime, om, first_investment]
        if project_life == lifetime:
            number_of_investments = 1
        else:
            number_of_investments = int(round(project_life / lifetime + 0.5))
        # costs with quantity and import tax at t=0
        first_time_investment = investment_t0 * (1 + tax)

        for count_of_replacements in range(0, number_of_investments):
            # Very first investment is in year 0
            if count_of_replacements == 0:
                capex = first_time_investment
            else:
                # replacements taking place in year = number_of_replacement * lifetime
                if count_of_replacements * lifetime != project_life:
                    capex = capex + first_time_investment / (
                        (1 + wacc) ** (count_of_replacements * lifetime)
                    )

        # Substraction of component value at end of life with last replacement (= number_of_investments - 1)
        if number_of_investments * lifetime > project_life:
            last_investment = first_time_investment / (
                (1 + wacc) ** ((number_of_investments - 1) * lifetime)
            )
            linear_depreciation_last_investment = last_investment / lifetime
            capex = capex - linear_depreciation_last_investment * (
                number_of_investments * lifetime - project_life
            )

        return capex

    def annuity(self, present_value, crf):
        """

        Parameters
        ----------
        present_value
        crf

        Returns
        -------

        """
        annuity = present_value * crf
        return annuity

    def present_value_from_annuity(self, annuity, annuity_factor):
        """

        Parameters
        ----------
        annuity
        annuity_factor

        Returns
        -------

        """
        present_value = annuity * annuity_factor
        return present_value

    def fuel_price_present_value(self, economics,):
        """
        
        Parameters
        ----------
        economics

        Returns
        -------

        """
        cash_flow_fuel_l = 0
        fuel_price_i = economics["fuel_price"]
        # todo check this calculation again!
        if economics["fuel_price_change_annual"] == 0:
            economics.update({"price_fuel": fuel_price_i})
        else:
            for i in range(0, economics["project_lifetime"]):
                cash_flow_fuel_l += fuel_price_i / (1 + economics["wacc"]) ** (i)
                fuel_price_i = fuel_price_i * (
                    1 + economics["fuel_price_change_annual"]
                )
            economics.update({"price_fuel": cash_flow_fuel_l * economics["crf"]})
