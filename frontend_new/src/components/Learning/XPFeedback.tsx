import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, X, Clock, ArrowRight } from 'lucide-react';
import { clsx } from 'clsx';
import type { XPReward, WordMastery } from '../../types';

interface XPFeedbackProps {
    isOpen: boolean;
    correct: boolean;
    /** Titre de l'en-tête : « Scrabble ! », « Autre scrabble accepté », « Solution révélée ». */
    title: string;
    /** Le mot, sous le titre - joué si correct, attendu sinon. */
    word?: string;
    xp: XPReward;
    mastery?: WordMastery;
    /**
     * Le débriefing du coup : mots formés, score obtenu, meilleur collage.
     * Voir la bonne réponse ne suffit pas — encore faut-il savoir ce que le
     * coup joué valait.
     */
    details?: React.ReactNode;
    /** Libellé du bouton : « Continuer » n'a pas de sens si le coup est montré. */
    continueLabel?: string;
    onContinue: () => void;
    /** Action secondaire, au-dessus du bouton principal (ex. « Voir le meilleur scrabble »). */
    secondaryAction?: { label: string; onClick: () => void };
}

export const XPFeedback: React.FC<XPFeedbackProps> = ({
    isOpen,
    correct,
    title,
    word,
    xp,
    mastery,
    details,
    continueLabel = 'Continuer',
    onContinue,
    secondaryAction
}) => {
    const lignesXP = xp.breakdown.map(line => {
        const points = line.match(/^\+\d+ XP/)?.[0] ?? '';
        const raison = line.replace(/^\+\d+ XP\s*/, '').replace(/[()]/g, '');
        return { points, raison: raison.charAt(0).toUpperCase() + raison.slice(1) };
    });

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                    onClick={onContinue}
                >
                    <motion.div
                        initial={{ scale: 0.8, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                        exit={{ scale: 0.8, y: 20 }}
                        onClick={(e) => e.stopPropagation()}
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="xp-feedback-titre"
                        className="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden tabular-nums"
                    >
                        {/* En-tête : le verdict, puis le mot */}
                        <div className={clsx(
                            "px-6 py-5 flex items-center gap-4",
                            correct ? "bg-emerald-500" : "bg-red-500"
                        )}>
                            <div className="shrink-0 w-11 h-11 rounded-full bg-white/20 flex items-center justify-center">
                                {correct
                                    ? <Check className="w-6 h-6 text-white" strokeWidth={3} />
                                    : <X className="w-6 h-6 text-white" strokeWidth={3} />}
                            </div>
                            <div className="min-w-0">
                                <h3 id="xp-feedback-titre" className="font-bold text-white text-xl leading-tight">
                                    {title}
                                </h3>
                                {word && (
                                    <p className="mt-0.5 font-mono font-bold text-white/90 tracking-[0.2em] truncate">
                                        {word}
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* Le coup : ce qui compte d'abord pour un joueur de scrabble */}
                        {details && <div className="px-6 py-4">{details}</div>}

                        {/* L'XP gagnée, en second plan */}
                        {correct && xp.total > 0 && (
                            <div className="mx-6 border-t border-slate-100 py-4 space-y-1.5 text-sm">
                                {lignesXP.map((l, i) => (
                                    <div key={i} className="flex items-center justify-between">
                                        <span className="text-slate-500">{l.raison}</span>
                                        <span className="font-semibold text-slate-700">{l.points}</span>
                                    </div>
                                ))}
                                <div className="flex items-center justify-between pt-1.5">
                                    <span className="font-bold text-slate-800">Total</span>
                                    <span className="font-bold text-lg text-emerald-600">+{xp.total} XP</span>
                                </div>
                            </div>
                        )}

                        {/* Actions, avec la prochaine révision juste au-dessus */}
                        <div className="px-6 pb-6 pt-2 flex flex-col gap-2">
                            {correct && mastery?.dueDate && (
                                <p className="flex items-center justify-center gap-1.5 text-xs text-slate-400 pb-1">
                                    <Clock className="w-3.5 h-3.5" />
                                    Prochaine révision {formatDueDate(mastery.dueDate)}
                                </p>
                            )}
                            {!correct && (
                                <p className="text-center text-xs text-slate-400 pb-1">
                                    Ce tirage reviendra bientôt pour bien l'ancrer.
                                </p>
                            )}
                            {secondaryAction && (
                                <button
                                    onClick={secondaryAction.onClick}
                                    className="w-full py-2.5 rounded-xl font-bold text-emerald-700 bg-emerald-50 border border-emerald-200
                                               hover:bg-emerald-100 transition-colors"
                                >
                                    {secondaryAction.label}
                                </button>
                            )}
                            <button
                                onClick={onContinue}
                                autoFocus
                                className={clsx(
                                    "w-full py-3 rounded-xl font-bold text-white flex items-center justify-center gap-2 transition-colors",
                                    correct ? "bg-emerald-500 hover:bg-emerald-600" : "bg-slate-700 hover:bg-slate-800"
                                )}
                            >
                                {continueLabel} <ArrowRight className="w-4 h-4" />
                            </button>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

function formatDueDate(isoDate: string): string {
    const due = new Date(isoDate);
    const now = new Date();
    const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    if (diffDays <= 0) return "aujourd'hui";
    if (diffDays === 1) return "demain";
    return `dans ${diffDays} jours`;
}
