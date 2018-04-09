<template>
  <div>
    <input type="hidden" name="form.field.extra_questions" v-bind:value="vv">

    <table class="table table-striped table-bordered">
      <tr>
          <th>Frage</th>
          <th>Typ</th>
      <th>Antwort(en)</th>
      <th></th>
      </tr>
      <tr v-for="q in questions" :key="q.question">
        <td>{{q.question}}</td>
        <td>{{q.type}}</td>
    <td> <ul v-for="a in q.answers" :key="a.value"> <li>{{a.value}}</li> </ul> </td>
    <td><a v-on:click="delete_question(q)">löschen</a></td>
      </tr>
    </table>

    <button type="button" class="btn btn-primary btn-lg" data-toggle="modal" data-target="#extra_fields_widget">
      Zusatzfragen hinzufügen
    </button>

    <div class="modal fade" tabindex="-1" role="dialog" id="extra_fields_widget" :class="{ in: modalShown }">
      <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal"
            aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <h4 class="modal-title">Zusatzfrage erfassen</h4>
      </div>
      <div class="modal-body">
        <form @submit.prevent="save_question">
              <div class="form-group">
        <label for="exampleInputName2">Frage</label>
        <input v-model="question.question"
               type="text" class="form-control"
               id="exampleInputName2" placeholder="Bitte geben Sie hier Ihre Frage ein" />
              </div>
              <div class="form-group">
        <label for="exampleInputEmail2">Type</label>
        <select v-model="question.type" v-on:change="may_need_answers" class="form-control" id="exampleInputEmail2">
          <option value="choice" selected="selected">Einen Wert auswählen</option>
          <option value="multi">Mehrere Werte auswählen</option>
          <option value="bool">Wahr oder Falsch</option>
        </select>
              </div>
              <div class="form-group" v-if="question.need_answers">
        <label for="exampleInputEmail2">Antworten</label>
        <div v-for="answer in question.answers" v-bind:key="answer">
          <input v-model="answer.value" />
          <button class="btn btn-default" v-on:click.prevent="remove_answer(answer)">
                    <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>
          </button>
        </div>
        
        <button type="submit" class="btn btn-default" v-on:click.prevent="add_answer">Antwort hinzufügen</button>
          </div>
          <hr />
          <div>
        <button type="submit" class="btn btn-default">Frage Speichern</button>
          </div>
        </form>
      </div>
      <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal">Schließen</button>
      </div>
    </div><!-- /.modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->
  </div>
</template>

<script>
/* eslint-disable */
let QUESTION = {
    question: '',
    type: '',
    need_answers: false,
    answers: []
}

function check_answer(answer) {
    if (answer.replace(/^\s+|\s+$/g, '')) {
	return answer.includes('::');
    }
    return false;
}

export default {
    methods: {
        showModal() {
            this.modalShown = !this.modalShown;
        },
	delete_question(q) {
            this.questions = this.questions.filter(
		(question) => question != q)
	},
        save_all() {
            var ss = ""
            this.questions.forEach(
		element => {
		    if (element.need_answers) {
			let choices = []
			element.answers.forEach(function (answer) {
			    let value = answer.value.trim();
			    if (value.length) {
				choices.push(value);
			    }
			});
			ss = (element.question.trim() + ' => ' +
			      element.type.trim() + '::' +
			      choices.join('::'))
		    }
		    else {
			ss = (element.question.trim() + ' => ' +
			      element.type.trim())
		    }
		    this.vv = ss
		}
            )
        },
	remove_answer(answer) {
            this.question.answers = this.question.answers.filter(
		(a) => a != answer)
	},
	may_need_answers(e) {
            this.question.need_answers = ['choice', 'multi'].includes(
		this.question.type)
            if (!this.question.need_answers) {
		this.question.answers = []
            }
	},
        save_question() {
            var error = false;
            if (!this.question.question.trim()) {
		error = true;
		alert('Please fill the question.');
            }
            if (!this.question.type.trim()) {
		error = true;
		alert('Please select a type of question.');
            }
            else if (this.question.need_answers) {
		let choices = []
		this.question.answers.forEach(function (answer) {
		    let value = answer.value.trim();
		    if (value.length) {
			choices.push(value);
		    }
		});
		if (choices.length < 2) {
		    alert('Please add at least 2 non-empty choices.');
		    error = true;
		}
            }
            if (!error) {
		this.questions.push(
		    Object.assign({}, this.question)
		)
		this.question.question=''
		this.question.type=''
                this.question.answers=[]
                this.save_all()
            }
        },
        add_answer() {
            this.question.answers.push(Object({value: ''}));
        }
    },
    data() {
	return {
            vv: '',
            modalShown: false,
            questions: [],
            question: QUESTION
	}
    }
}
</script>
    
<style scoped>

</style>
