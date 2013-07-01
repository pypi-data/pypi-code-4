from base import IfbyphoneApiBase

class Survo(IfbyphoneApiBase):

    def delete_survey_results(self, **kwargs):
        """Delete all SurVo results for a single SurVo
        
        keyword arguments:
        survo_id -- unique ID for the survo
        before_date -- (optional) Restricts the delete 
                        operation to results prior to the specified date
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'survo.delete_survey_results'
        return self.call(self.options)
    
    def get_recording(self, **kwargs):
        """Retreive an audio recording made at an IVR level
        
        keyword arguments:
        format      -- 'wav' 'mp3'
        survo_id    -- unique ID of SurVo
        unique_id   -- unique ID of caller on SurVo
        question    -- question number for question where recording was taken
        sample_rate -- audio rate of streaming data
        
        """
        
        self.option.update(kwargs)
        self.option['action'] = 'survo.get_recording'
        return self.call(self.options)